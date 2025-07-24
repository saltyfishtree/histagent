import { Attachment } from '../types';
import { useAppStore } from '../store';

class FileUploadService {
  private maxFileSize = 50 * 1024 * 1024; // 50MB
  private allowedTypes = [
    'image/*',
    'application/pdf',
    'text/*',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'audio/*',
    'video/*'
  ];

  async uploadFile(file: File): Promise<Attachment> {
    // 验证文件
    this.validateFile(file);

    const fileId = this.generateFileId();
    const store = useAppStore.getState();

    // 创建上传进度记录
    store.addUploadProgress({
      fileId,
      progress: 0,
      status: 'uploading',
    });

    try {
      // 创建FormData
      const formData = new FormData();
      formData.append('file', file);
      formData.append('fileId', fileId);

      // 上传文件
      const response = await this.uploadWithProgress(formData, fileId);

      if (!response.ok) {
        throw new Error(`上传失败: ${response.statusText}`);
      }

      const result = await response.json();

      // 更新上传状态
      store.updateUploadProgress(fileId, {
        progress: 100,
        status: 'completed',
      });

      // 清除上传进度记录
      setTimeout(() => {
        store.removeUploadProgress(fileId);
      }, 2000);

      // 创建附件对象
      const attachment: Attachment = {
        id: fileId,
        name: file.name,
        type: file.type,
        size: file.size,
        url: result.url,
      };

      return attachment;

    } catch (error) {
      // 更新错误状态
      store.updateUploadProgress(fileId, {
        status: 'error',
        error: error instanceof Error ? error.message : '上传失败',
      });

      // 5秒后清除错误记录
      setTimeout(() => {
        store.removeUploadProgress(fileId);
      }, 5000);

      throw error;
    }
  }

  async uploadFiles(files: FileList | File[]): Promise<Attachment[]> {
    const fileArray = Array.from(files);
    const uploadPromises = fileArray.map(file => this.uploadFile(file));
    
    try {
      const results = await Promise.allSettled(uploadPromises);
      const attachments: Attachment[] = [];
      const errors: string[] = [];

      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          attachments.push(result.value);
        } else {
          errors.push(`${fileArray[index].name}: ${result.reason.message}`);
        }
      });

      if (errors.length > 0) {
        console.warn('部分文件上传失败:', errors);
      }

      return attachments;

    } catch (error) {
      console.error('批量上传文件失败:', error);
      throw error;
    }
  }

  private uploadWithProgress(formData: FormData, fileId: string): Promise<Response> {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      // 监听上传进度
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          useAppStore.getState().updateUploadProgress(fileId, { progress });
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(new Response(xhr.responseText, {
            status: xhr.status,
            statusText: xhr.statusText,
            headers: new Headers({
              'Content-Type': 'application/json',
            }),
          }));
        } else {
          reject(new Error(`HTTP Error: ${xhr.status}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('网络错误'));
      });

      xhr.addEventListener('abort', () => {
        reject(new Error('上传已取消'));
      });

      xhr.open('POST', 'http://localhost:8000/api/upload');
      xhr.send(formData);
    });
  }

  private validateFile(file: File): void {
    // 检查文件大小
    if (file.size > this.maxFileSize) {
      throw new Error(`文件大小超过限制 (${Math.round(this.maxFileSize / 1024 / 1024)}MB)`);
    }

    // 检查文件类型
    const isValidType = this.allowedTypes.some(type => {
      if (type.endsWith('/*')) {
        const category = type.slice(0, -2);
        return file.type.startsWith(category);
      }
      return file.type === type;
    });

    if (!isValidType) {
      throw new Error(`不支持的文件类型: ${file.type}`);
    }
  }

  private generateFileId(): string {
    return Math.random().toString(36).substring(2) + Date.now().toString(36);
  }

  // 获取文件图标
  getFileIcon(fileType: string): string {
    if (fileType.startsWith('image/')) return 'image';
    if (fileType.startsWith('video/')) return 'videocam';
    if (fileType.startsWith('audio/')) return 'audiotrack';
    if (fileType.includes('pdf')) return 'picture_as_pdf';
    if (fileType.includes('word') || fileType.includes('document')) return 'description';
    if (fileType.includes('excel') || fileType.includes('spreadsheet')) return 'table_chart';
    if (fileType.startsWith('text/')) return 'text_snippet';
    return 'attach_file';
  }

  // 格式化文件大小
  formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  // 检查文件是否为图片
  isImage(fileType: string): boolean {
    return fileType.startsWith('image/');
  }

  // 检查文件是否为视频
  isVideo(fileType: string): boolean {
    return fileType.startsWith('video/');
  }

  // 检查文件是否为音频
  isAudio(fileType: string): boolean {
    return fileType.startsWith('audio/');
  }
}

// 创建单例实例
export const fileUploadService = new FileUploadService();

// 导出默认实例
export default fileUploadService; 