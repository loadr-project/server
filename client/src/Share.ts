import {Downloader} from "./Downloader";

export interface ShareResponse {
  file: File,
  shareError: string|null
}
interface NavigatorShareFile {
  files: File[],
  title: string
}

export class Share {

  private canShare(shareFile: NavigatorShareFile): boolean {
    // @ts-ignore
    if(!navigator.canShare) {
      return false;
    }
    // @ts-ignore
    if(!navigator.canShare(shareFile)) {
      return false;
    }
    return true;
  }

  public processFile(file: File): Promise<ShareResponse> {
    const shareFile: NavigatorShareFile = {
      files: [file],
      title: file.name
    };
    const shareResponse: ShareResponse = {
      file: file,
      shareError: null
    };
    // TODO: return share Promise as soon as type is known of navigator.share
    return new Promise<ShareResponse>(resolve => {
      if(this.canShare(shareFile)) {
        // @ts-ignore
        navigator.share(shareFile)
          .then(() => resolve(shareResponse))
          .catch((shareError: any) => {
            console.error("navigator.share failed: ", shareError);
            shareResponse.shareError = shareError;
            resolve(shareResponse);
          });
      } else {
        this.downloadFile(file);
        resolve(shareResponse);
      }
    });
  }

  private downloadFile(file: File) {
    let a = document.createElement("a");
    document.body.appendChild(a);
    let url = window.URL.createObjectURL(file);
    a.href = url;
    a.download = file.name;
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
  }

  public share(url: string): Promise<ShareResponse> {
    const downloader = new Downloader(url);
    return downloader
      .loadFile()
      .then(file => this.processFile(file));
  }
}

