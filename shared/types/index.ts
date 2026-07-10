export type UserRole = 'admin' | 'member' | 'viewer';

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  role: UserRole;
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  ownerId: string;
  status: 'draft' | 'active' | 'archived';
  createdAt: string;
  updatedAt: string;
}

export interface Document {
  id: string;
  title: string;
  content: string;
  projectId: string;
  authorId: string;
  version: number;
  createdAt: string;
  updatedAt: string;
}

export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
  error?: string;
  traceId?: string;
}

export interface CodePlan {
  id: string;
  workspaceId: string;
  title: string;
  description?: string;
  scope: Record<string, any>;
  steps: string[];
  status: string;
  createdAt: string;
  updatedAt: string;
}

export interface GeneratedCodeFile {
  id: string;
  workspaceId: string;
  projectId?: string;
  filePath: string;
  fileType: string;
  content: string;
  language: string;
  isMerged: boolean;
  createdAt: string;
}

export interface CodeReview {
  id: string;
  workspaceId: string;
  filePath: string;
  status: string;
  reviewer: string;
  comments: Array<Record<string, any>>;
  score: number;
  createdAt: string;
}

export interface CodeQualityScan {
  id: string;
  workspaceId: string;
  complexityScore: number;
  duplicationRate: number;
  testCoverageEst: number;
  securityVulnerabilities: Array<Record<string, any>>;
  styleViolations: Array<Record<string, any>>;
  createdAt: string;
}

export interface RefactoringProposal {
  id: string;
  workspaceId: string;
  filePath: string;
  originalCode: string;
  refactoredCode: string;
  rationale: string;
  status: string;
  createdAt: string;
}

export interface BugReport {
  id: string;
  workspaceId: string;
  title: string;
  description?: string;
  severity: string;
  detectedAt: string;
  suggestedFix?: string;
  status: string;
  createdAt: string;
}

export interface GitBranchObj {
  id: string;
  workspaceId: string;
  branchName: string;
  sourceBranch: string;
  status: string;
  createdAt: string;
}

export interface GitCommitObj {
  id: string;
  workspaceId: string;
  branchId: string;
  commitHash: string;
  commitMessage: string;
  author: string;
  filesChanged: string[];
  createdAt: string;
}

export interface GitPRObj {
  id: string;
  workspaceId: string;
  title: string;
  description?: string;
  sourceBranch: string;
  targetBranch: string;
  status: string;
  mergeRecommendation: string;
  createdAt: string;
}

export interface ReleasePlanObj {
  id: string;
  workspaceId: string;
  version: string;
  name: string;
  description?: string;
  milestones: Array<Record<string, any>>;
  scope: string[];
  status: string;
  createdAt: string;
}

export interface DeploymentPlanObj {
  id: string;
  workspaceId: string;
  releaseId: string;
  environment: string;
  provider: string;
  manifests: Record<string, any>;
  steps: string[];
  status: string;
  createdAt: string;
}

export interface CEOReport {
  id: string;
  workspaceId: string;
  title: string;
  strategyData: Record<string, any>;
  portfolioData: Record<string, any>;
  financials: Record<string, any>;
  marketIntelligence: Record<string, any>;
  recommendations: Array<Record<string, any>>;
  marketingSales: Record<string, any>;
  createdAt: string;
}

export interface CTOReport {
  id: string;
  workspaceId: string;
  title: string;
  architectureReview: Record<string, any>;
  optimizationPlans: Record<string, any>;
  securityDevops: Record<string, any>;
  technicalDebt: Record<string, any>;
  healthMetrics: Record<string, any>;
  createdAt: string;
}

export interface COOReport {
  id: string;
  workspaceId: string;
  title: string;
  resourceCapacity: Record<string, any>;
  deliveryMonitoring: Record<string, any>;
  incidentsRisks: Record<string, any>;
  operationsAnalytics: Record<string, any>;
  notificationCenter: Array<Record<string, any>>;
  createdAt: string;
}


