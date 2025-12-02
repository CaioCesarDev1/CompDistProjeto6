// Declaração de tipos para o módulo soap
declare module 'soap' {
  import { Server } from 'http';
  
  export interface Service {
    [key: string]: any;
  }
  
  export interface WSDL {
    [key: string]: any;
  }
  
  export function listen(
    app: any,
    path: string,
    services: any,
    wsdl: string,
    callback?: () => void
  ): void;
  
  export function createClient(
    wsdl: string,
    options?: any,
    callback?: (err: any, client: any) => void
  ): void;
}

