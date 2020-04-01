import contentDisposition from "content-disposition"

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
          const contentDispositionValue = headers.get("content-disposition");
          if(contentDispositionValue === null) {
            reject("Content-Disposition empty!");
            return;
          }
          const parsedContentDisposition = contentDisposition.parse(contentDispositionValue);
          const fileName = parsedContentDisposition.parameters.filename;

          if(!fileName) {
            reject("Can't get filename from Content-Disposition!");
            return;
          }

          const contentType = headers.get("content-type");
          if(contentType === null) {
            reject("Content-Type empty!");
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
}
