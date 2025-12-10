import os
import tempfile
import uuid
from werkzeug.utils import secure_filename
from app.service.r2_helper import r2_helper

class R2Mixin:
    """
    Mixin class to provide R2 functionality for controllers
    """

    def __init__(self, controller_name=None):
        self.controller_name = controller_name or self.__class__.__name__.replace('Controller', '').lower()

    def process_file_with_r2(self, file, process_function, **process_kwargs):
        """
        Generic method to process files using R2 storage

        Args:
            file: Uploaded file object
            process_function: Function to process the file (should take input_path, output_path, **kwargs)
            **process_kwargs: Additional arguments for the process function

        Returns:
            dict: {
                'success': bool,
                'output_key': str or None,
                'message': str,
                'download_url': str or None
            }
        """
        try:
            # Generate UID
            uid = str(uuid.uuid4())
            filename = secure_filename(file.filename)

            # Upload original file to R2
            upload_result = r2_helper.upload_file(
                file,
                filename=filename,
                folder=self.controller_name
            )

            if not upload_result['success']:
                return {
                    'success': False,
                    'message': f"Failed to upload file: {upload_result['message']}"
                }

            input_key = upload_result['file_key']

            # Download file for processing
            download_result = r2_helper.download_file(input_key)

            if not download_result['success']:
                return {
                    'success': False,
                    'message': f"Failed to download file for processing: {download_result['message']}"
                }

            # Create temporary files
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp_input:
                tmp_input.write(download_result['file_obj'].read())
                temp_input_path = tmp_input.name

            # Create temporary output path
            temp_output_path = tempfile.mktemp(suffix='_processed' + os.path.splitext(filename)[1])

            try:
                # Process the file
                processed_filename = process_function(
                    filename,
                    temp_input_path,
                    temp_output_path,
                    **process_kwargs
                )

                # Upload processed file to R2
                output_upload_result = r2_helper.upload_file(
                    temp_output_path,
                    filename=processed_filename,
                    folder=self.controller_name
                )

                if not output_upload_result['success']:
                    return {
                        'success': False,
                        'message': f"Failed to upload processed file: {output_upload_result['message']}"
                    }

                return {
                    'success': True,
                    'output_key': output_upload_result['file_key'],
                    'message': 'File processed successfully',
                    'download_url': output_upload_result['file_url']
                }

            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_input_path)
                    if os.path.exists(temp_output_path):
                        os.unlink(temp_output_path)
                except:
                    pass

        except Exception as e:
            return {
                'success': False,
                'message': f"Error processing file: {str(e)}"
            }

    def batch_process_with_r2(self, files, process_function, **process_kwargs):
        """
        Process multiple files using R2 storage

        Args:
            files: List of uploaded file objects
            process_function: Function to process each file
            **process_kwargs: Additional arguments for the process function

        Returns:
            dict: {
                'success': bool,
                'results': list,
                'message': str
            }
        """
        results = []

        for file in files:
            result = self.process_file_with_r2(file, process_function, **process_kwargs)
            results.append({
                'filename': file.filename,
                'result': result
            })

        successful = sum(1 for r in results if r['result']['success'])
        total = len(results)

        return {
            'success': successful > 0,
            'results': results,
            'message': f"Processed {successful}/{total} files successfully"
        }

    def create_zip_from_r2_files(self, file_keys, zip_filename=None):
        """
        Create a ZIP file from multiple R2 files

        Args:
            file_keys: List of R2 file keys
            zip_filename: Name for the ZIP file (optional)

        Returns:
            dict: {
                'success': bool,
                'zip_key': str or None,
                'message': str
            }
        """
        try:
            if zip_filename is None:
                zip_filename = f"archive_{uuid.uuid4().hex}.zip"

            import zipfile

            # Create temporary ZIP file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
                with zipfile.ZipFile(tmp_zip.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_key in file_keys:
                        # Download file from R2
                        download_result = r2_helper.download_file(file_key)

                        if download_result['success']:
                            # Add to ZIP
                            file_content = download_result['file_obj'].read()
                            zipf.writestr(os.path.basename(file_key), file_content)

                temp_zip_path = tmp_zip.name

            # Upload ZIP to R2
            upload_result = r2_helper.upload_file(
                temp_zip_path,
                filename=zip_filename,
                folder='zip'
            )

            # Clean up temporary file
            os.unlink(temp_zip_path)

            if upload_result['success']:
                return {
                    'success': True,
                    'zip_key': upload_result['file_key'],
                    'message': 'ZIP file created successfully'
                }
            else:
                return {
                    'success': False,
                    'message': f"Failed to upload ZIP file: {upload_result['message']}"
                }

        except Exception as e:
            return {
                'success': False,
                'message': f"Error creating ZIP file: {str(e)}"
            }

    def move_processed_file(self, source_key, destination_folder=None):
        """
        Move processed file to destination folder

        Args:
            source_key: Source R2 file key
            destination_folder: Destination folder (optional)

        Returns:
            dict: {
                'success': bool,
                'destination_key': str or None,
                'message': str
            }
        """
        try:
            if destination_folder is None:
                destination_folder = f"{self.controller_name}/processed"

            filename = os.path.basename(source_key)
            destination_key = f"{destination_folder}/{filename}"

            result = r2_helper.move_file(source_key, destination_key)

            if result['success']:
                return {
                    'success': True,
                    'destination_key': destination_key,
                    'message': 'File moved successfully'
                }
            else:
                return result

        except Exception as e:
            return {
                'success': False,
                'message': f"Error moving file: {str(e)}"
            }

    def cleanup_temp_files(self, file_keys):
        """
        Clean up temporary files from R2

        Args:
            file_keys: List of file keys to delete

        Returns:
            dict: {
                'success': bool,
                'deleted_count': int,
                'message': str
            }
        """
        deleted_count = 0
        errors = []

        for file_key in file_keys:
            result = r2_helper.delete_file(file_key)
            if result['success']:
                deleted_count += 1
            else:
                errors.append(f"Failed to delete {file_key}: {result['message']}")

        return {
            'success': deleted_count > 0,
            'deleted_count': deleted_count,
            'message': f"Deleted {deleted_count}/{len(file_keys)} files successfully",
            'errors': errors
        }