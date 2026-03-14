from __future__ import annotations


class CameraUnavailableError(RuntimeError):
    pass


class OpenCVCameraSource:
    def __init__(self, index: int = 0) -> None:
        try:
            import cv2  # type: ignore
        except ImportError as exc:
            raise CameraUnavailableError(
                "opencv-python is not installed. Install with: pip install -e .[vision]"
            ) from exc
        self._cv2 = cv2
        self._cap = cv2.VideoCapture(index)
        if not self._cap.isOpened():
            raise CameraUnavailableError(f"Could not open camera index {index}.")

    def read_frame(self):
        ok, frame = self._cap.read()
        if not ok:
            raise CameraUnavailableError("Failed to read frame from camera.")
        return frame

    def close(self) -> None:
        self._cap.release()
