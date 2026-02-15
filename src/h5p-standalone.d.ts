declare module 'h5p-standalone' {
  export class H5P {
    constructor(el: HTMLElement, options: Record<string, unknown>);
    then(callback: (id: string) => void): H5P;
  }
}
