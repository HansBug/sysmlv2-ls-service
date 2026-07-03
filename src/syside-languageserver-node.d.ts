declare module "syside-languageserver/node" {
  export * from "syside-languageserver/lib/node/index";
}

declare module "syside-languageserver/lib/node/node-file-system-provider.js" {
  import type { SysMLFileSystemProvider } from "syside-languageserver/lib/services/shared/workspace/file-system-provider";

  export class SysMLNodeFileSystemProvider implements SysMLFileSystemProvider {
    get standardLibrary(): import("vscode-uri").URI | undefined;
    get extensionDir(): import("vscode-uri").URI | undefined;
    updateStandardLibrary(value: string | undefined): void;
    exists(path: import("vscode-uri").URI): Promise<boolean>;
    existsSync(path: import("vscode-uri").URI): boolean;
    loadScript(path: import("vscode-uri").URI): Promise<object | undefined>;
    preloadFiles(paths?: readonly import("vscode-uri").URI[]): Promise<void>;
  }

  export const SysMLNodeFileSystem: {
    fileSystemProvider: () => SysMLFileSystemProvider;
  };
}
