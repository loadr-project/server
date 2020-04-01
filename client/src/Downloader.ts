export class Downloader {
  private readonly url: string;
  constructor(url: string) {
    this.url = url;
  }
  public loadFile(): Promise<File> {
    return new Promise<File>(((resolve, reject) => {
      // TODO: make API URL configurable
      fetch("https://api." + window.location.host + "?url=" + this.url)
        .then(async response => {
          const headers = response.headers;
          const contentDisposition = headers.get("content-disposition");
          const contentType = headers.get("content-type");
          if(contentType === null) {
            reject("Content-Type empty!");
            return;
          }
          let fileName;
          try {
            fileName = this.getFilename(contentDisposition)
          } catch (error) {
            reject(error);
            return;
          }
          if(response.status !== 200) {
            reject(await response.text());
            return;
          }
          const blob = await response.blob();
          resolve(new File([blob], fileName, {type: contentType}));
        })
        .catch(reject);
    }))
  }

  private getFilename(contentDisposition: string|null): string {
    if(contentDisposition === null) {
      throw new Error("Content-Disposition empty!");
    }
    const parts = contentDisposition.split(";");

    if(parts.length < 2) {
      throw new Error("Unexpected Content-Disposition: " + contentDisposition);
    }
    const prefix = ' filename="';
    const appendix = '"';
    const part = parts[1];
    if(!part.startsWith(prefix) || !part.endsWith(appendix)) {
      throw new Error("Unexpected Content-Disposition: " + contentDisposition);
    }
    return part.slice(prefix.length, part.length - appendix.length);
  }
}
