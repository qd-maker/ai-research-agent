import axios from "axios";

// Types
export interface ResearchRequest {
    query: string;
}

export interface ResearchResponse {
    job_id: string;
    query: string;
    status: string;
    message: string;
}

export interface JobStatus {
    job_id: string;
    query: string;
    status: "pending" | "running" | "completed" | "failed";
    progress: string;
    step_count: number;
    max_steps: number;
    errors: string[];
    created_at: string;
    updated_at: string;
}

export interface JobReport {
    job_id: string;
    query: string;
    status: string;
    report_md: string;
    report_json: Record<string, unknown>;
}

// API Client
const API_BASE_URL = "http://localhost:8000/api/v1";

export const api = {
    // Create a new research job
    createJob: async (query: string): Promise<ResearchResponse> => {
        const response = await axios.post(`${API_BASE_URL}/research`, { query });
        return response.data;
    },

    // Get job status
    getJobStatus: async (jobId: string): Promise<JobStatus> => {
        const response = await axios.get(`${API_BASE_URL}/jobs/${jobId}`);
        return response.data;
    },

    // Get job report
    getJobReport: async (jobId: string): Promise<JobReport> => {
        const response = await axios.get(`${API_BASE_URL}/reports/${jobId}`);
        return response.data;
    },

    // Download links (helpers)
    getDownloadLinks: (jobId: string) => ({
        markdown: `${API_BASE_URL}/reports/${jobId}/markdown`,
        csv: `${API_BASE_URL}/reports/${jobId}/csv`,
    }),
};
