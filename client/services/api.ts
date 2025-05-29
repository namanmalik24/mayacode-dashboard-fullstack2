// API service for backend communication
const API_BASE_URL = 'http://127.0.0.1:8000';

interface ApiResponse<T> {
  success: boolean;
  data: T;
  timestamp: string;
  error?: string;
  message?: string;
}

interface PaginationInfo {
  currentPage: number;
  totalItems: number;
  itemsPerPage: number;
  totalPages: number;
  hasMore: boolean;
  nextPage: number | null;
  isInitialLoad: boolean;
}

interface ActionsResponse {
  actions: any[];
  pagination: PaginationInfo;
}

interface DocumentsResponse {
  documents: any[];
  pagination: PaginationInfo;
}

interface DashboardSummaryResponse {
  user: any;
  stats: {
    totalActions: number;
    completedActions: number;
    inProgressActions: number;
    notStartedActions: number;
    onboardingCompletion: number;
    totalDocuments: number;
  };
  recentActions: any[];
  recentDocuments: any[];
}

class ApiService {
  private async fetchApi<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // Get user data (profile)
  async getUser() {
    return this.fetchApi<any>('/user');
  }

  // Get user actions with progressive loading
  async getUserActions(params: {
    page?: number;
    limit?: number;
    status?: string;
    loadMore?: boolean;
  } = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.status) queryParams.append('status', params.status);
    if (params.loadMore !== undefined) queryParams.append('loadMore', params.loadMore.toString());

    const endpoint = `/user/actions${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.fetchApi<ActionsResponse>(endpoint);
  }

  // Get specific action by ID
  async getActionById(id: string) {
    return this.fetchApi<any>(`/user/actions/${id}`);
  }

  // Get user documents with progressive loading
  async getUserDocuments(params: {
    page?: number;
    limit?: number;
    type?: string;
    loadMore?: boolean;
  } = {}) {
    const queryParams = new URLSearchParams();
    
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.limit) queryParams.append('limit', params.limit.toString());
    if (params.type) queryParams.append('type', params.type);
    if (params.loadMore !== undefined) queryParams.append('loadMore', params.loadMore.toString());

    const endpoint = `/user/documents${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    return this.fetchApi<DocumentsResponse>(endpoint);
  }

  // Get PDF as base64 from backend and return a Blob
  async getPdfBlob() {
    const response = await this.fetchApi<any>('/pdf');
    if (response.success && response.data) {
      const byteCharacters = atob(response.data);
      const byteNumbers = new Array(byteCharacters.length);
      for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      return new Blob([byteArray], { type: 'application/pdf' });
    }
    throw new Error('Failed to fetch PDF');
  }

  // Chat with backend OpenAI endpoint
  async chatWithAssistant(messages: { role: string; content: string }[]) {
    const response = await this.fetchApi<any>('/chat', {
      method: 'POST',
      body: JSON.stringify({ messages }),
    });
    if (response.success && response.data) {
      return response.data;
    }
    throw new Error(response.detail || 'Failed to get assistant response');
  }

  // Health check
  async healthCheck() {
    return this.fetchApi<{ message: string; version: string }>('/health');
  }
}

export const apiService = new ApiService();
export type { ApiResponse, PaginationInfo, ActionsResponse, DocumentsResponse, DashboardSummaryResponse }; 