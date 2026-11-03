const TOKEN_KEY = "cleartitle_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null): void {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

export interface HealthStatus {
  status: string;
  sarvam_key: boolean;
}

export interface AuthUser {
  id: string;
  email: string;
  full_name?: string | null;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export interface UploadResponse {
  case_id: string;
  files: { doc_id: string; original_name: string; saved_path: string; size_kb: number }[];
}

export interface ProcessResponse {
  status: string;
  mode?: string;
}

export interface StatusResponse {
  status: string;
  progress?: number;
  completed_docs?: number;
  total_docs?: number;
  failed_docs?: number;
  log?: string[];
  errors?: any[];
  needs_action?: any[];
  files?: { doc_id: string; original_name: string; status: string; document_type: string }[];
}

export interface CaseListItem {
  id: string;
  status: string;
  completed_docs: number;
  total_docs: number;
  failed_docs?: number;
  created_at?: string;
}

export interface CasesResponse {
  cases: CaseListItem[];
  total: number;
}

export interface OcrDocText {
  doc_id: string;
  doc_index: number | null;
  filename: string | null;
  document_type: string | null;
  status: string | null;
  total_pages: number | null;
  full_text: string;
  available: boolean;
}

export interface OcrTextResponse {
  case_id: string;
  documents: OcrDocText[];
}

async function apiError(response: Response, fallback = "Request failed"): Promise<string> {
  const text = await response.text();
  if (!text) return fallback;
  try {
    const data = JSON.parse(text);
    if (typeof data.detail === "string") return data.detail;
    if (Array.isArray(data.detail)) return data.detail.map((d: any) => d.msg || JSON.stringify(d)).join("; ");
    return data.message || data.detail || fallback;
  } catch {
    return text;
  }
}

async function request<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const headers = new Headers(opts.headers);
  const token = getToken();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const body = opts.body;
  if (body && !(body instanceof FormData) && typeof body === "string") {
    headers.set("Content-Type", "application/json");
  }
  const r = await fetch(path, { ...opts, headers });
  if (!r.ok) throw new Error(await apiError(r));
  return r.json();
}

export const API = {
  async health(): Promise<HealthStatus> {
    try {
      const r = await fetch("/health");
      if (!r.ok) return { status: "error", sarvam_key: false };
      return r.json();
    } catch {
      return { status: "error", sarvam_key: false };
    }
  },

  async register(email: string, password: string, fullName?: string): Promise<AuthResponse> {
    return request<AuthResponse>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName || null }),
    });
  },

  async login(email: string, password: string): Promise<AuthResponse> {
    return request<AuthResponse>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
  },

  async me(): Promise<AuthResponse> {
    return request<AuthResponse>("/api/auth/me");
  },

  async upload(files: File[], slots?: string[]): Promise<UploadResponse> {
    const fd = new FormData();
    files.forEach((f, i) => {
      fd.append("files", f);
      if (slots) fd.append("slots", slots[i] ?? "");
    });
    return request<UploadResponse>("/api/upload", { method: "POST", body: fd });
  },

  async uploadMore(caseId: string, files: File[]): Promise<UploadResponse> {
    const fd = new FormData();
    files.forEach(f => fd.append("files", f));
    return request<UploadResponse>(`/api/case/${caseId}/upload`, { method: "POST", body: fd });
  },

  async process(caseId: string): Promise<ProcessResponse> {
    return request<ProcessResponse>(`/api/process/${caseId}`, { method: "POST" });
  },

  async status(caseId: string): Promise<StatusResponse> {
    try {
      return await request<StatusResponse>(`/api/status/${caseId}`);
    } catch {
      return { status: "unknown" };
    }
  },

  async retry(caseId: string) {
    return request(`/api/retry/${caseId}`, { method: "POST" });
  },

  async skipDoc(caseId: string, docId: string) {
    return request(`/api/case/${caseId}/doc/${docId}/skip`, { method: "POST" });
  },

  async replaceDoc(caseId: string, docId: string, file: File) {
    const fd = new FormData();
    fd.append("file", file);
    return request(`/api/case/${caseId}/doc/${docId}/replace`, { method: "POST", body: fd });
  },

  async deleteCase(caseId: string) {
    return request(`/api/case/${caseId}`, { method: "DELETE" });
  },

  async link(caseId: string): Promise<{ case_id: string; linked: boolean; already?: boolean }> {
    return request(`/api/case/${caseId}/link`, { method: "POST" });
  },

  async listCases(): Promise<CasesResponse> {
    try {
      return await request<CasesResponse>("/api/cases");
    } catch {
      return { cases: [], total: 0 };
    }
  },

  async getOcr(caseId: string): Promise<OcrTextResponse> {
    return request<OcrTextResponse>(`/api/results/${caseId}/ocr`);
  },
};
