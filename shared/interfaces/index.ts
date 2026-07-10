export interface IAuthService {
  login(credentials: any): Promise<any>;
  signup(data: any): Promise<any>;
  logout(): Promise<void>;
  getCurrentUser(): Promise<any>;
}

export interface IProjectService {
  getProjects(): Promise<any[]>;
  getProjectById(id: string): Promise<any>;
  createProject(data: any): Promise<any>;
  updateProject(id: string, data: any): Promise<any>;
  deleteProject(id: string): Promise<void>;
}

export interface IDocumentService {
  getDocuments(projectId: string): Promise<any[]>;
  getDocumentById(id: string): Promise<any>;
  createDocument(data: any): Promise<any>;
  updateDocument(id: string, data: any): Promise<any>;
  deleteDocument(id: string): Promise<void>;
}
