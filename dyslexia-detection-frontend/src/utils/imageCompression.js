export const compressImage = async (file, maxSizeMB = 1) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);

    reader.onload = (event) => {
      const img = new Image();
      img.src = event.target.result;

      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;

        // Calculate new dimensions while maintaining aspect ratio
        if (width > 2000 || height > 2000) {
          const ratio = Math.min(2000 / width, 2000 / height);
          width *= ratio;
          height *= ratio;
        }

        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#FFFFFF'; // Set white background
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0, width, height);

        // Convert to Blob with quality adjustment
        canvas.toBlob(
          (blob) => {
            if (!blob) {
              reject(new Error('Canvas to Blob conversion failed'));
              return;
            }

            // If the blob is still too large, reduce quality
            if (blob.size > maxSizeMB * 1024 * 1024) {
              const quality = Math.min(0.9, (maxSizeMB * 1024 * 1024) / blob.size);
              canvas.toBlob(
                (compressedBlob) => {
                  if (!compressedBlob) {
                    reject(new Error('Image compression failed'));
                    return;
                  }
                  resolve(new File([compressedBlob], file.name, {
                    type: 'image/jpeg',
                    lastModified: Date.now(),
                  }));
                },
                'image/jpeg',
                quality
              );
            } else {
              resolve(new File([blob], file.name, {
                type: 'image/jpeg',
                lastModified: Date.now(),
              }));
            }
          },
          'image/jpeg',
          0.9
        );
      };

      img.onerror = () => {
        reject(new Error('Failed to load image'));
      };
    };

    reader.onerror = () => {
      reject(new Error('Failed to read file'));
    };
  });
}; 