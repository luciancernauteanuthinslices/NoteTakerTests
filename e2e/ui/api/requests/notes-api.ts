import { APIRequestContext } from '@playwright/test';
import apiEndpoints from '../../utils/apiEndpoints';

export interface LoginResponse {
  success: boolean;
  status: number;
  message: string;
  data: {
    id: string;
    name: string;
    email: string;
    token: string;
  };
}

export interface NoteData {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  created_at: string;
  updated_at: string;
  category: string;
  user_id: string;
}

export interface CreateNoteResponse {
  success: boolean;
  status: number;
  message: string;
  data: NoteData;
}

export interface DeleteNoteResponse {
  success: boolean;
  status: number;
  message: string;
}

export interface GetUserProfileResponse{
    success: boolean;
    status: number;
    message: string;
    data: {
        id: string;
        name: string;
        email: string;
        phone: string;
        company: string;
    };
}

// Store baseUrl for use across API functions
let apiBaseUrl: string = '';

export function setApiBaseUrl(url: string): void {
  apiBaseUrl = url;
}

function getFullUrl(path: string): string {
  return apiBaseUrl ? `${apiBaseUrl}${path}` : path;
}

/**
 * Create a new note via API
 * POST /notes
 */
export async function createNote(
  apiContext: APIRequestContext,
  title: string,
  description: string,
  category: 'Home' | 'Work' | 'Personal'
): Promise<CreateNoteResponse> {
  const response = await apiContext.post(getFullUrl(apiEndpoints.notes.postNote), {
    form: {
      title,
      description,
      category,
    },
  });
  
  if (!response.ok()) {
    throw new Error(`Create note failed with status ${response.status()}: ${await response.text()}`);
  }
  
  return response.json();
}

/**
 * Delete a note by ID via API
 * DELETE /notes/{id}
 */
export async function deleteNoteById(
  apiContext: APIRequestContext,
  noteId: string
): Promise<DeleteNoteResponse> {
  const response = await apiContext.delete(getFullUrl(apiEndpoints.notes.deleteNote+noteId));
  
  if (!response.ok()) {
    throw new Error(`Delete note failed with status ${response.status()}: ${await response.text()}`);
  }
  
  return response.json();
}

/**
 * Get all notes via API
 * GET /notes
 */
export async function getAllNotes(apiContext: APIRequestContext): Promise<CreateNoteResponse> {
  const response = await apiContext.get(getFullUrl('/notes'));
  
  if (!response.ok()) {
    throw new Error(`Get all notes failed with status ${response.status()}: ${await response.text()}`);
  }
  
  return response.json();
}

/**
 * Login to get authentication token
 * POST /users/login
 */
export async function login(
  apiContext: APIRequestContext,
  email: string,
  password: string,
  baseUrl?: string
): Promise<LoginResponse> {
  // Use full URL to bypass any baseURL issues
  const url = baseUrl ? baseUrl+apiEndpoints.account.login : apiEndpoints.account.login;
  console.log(`Making login request to: ${url}`);
  
  const response = await apiContext.post(url, {
    form: {
      email,
      password,
    },
  });
  
  console.log(`Login response status: ${response.status()}`);
  
  if (!response.ok()) {
    throw new Error(`Login failed with status ${response.status()}: ${await response.text()}`);
  }
  
  return response.json();
}

//get user profile
export async function getUserProfile(
  apiContext: APIRequestContext,
): Promise<GetUserProfileResponse> {
  const response = await apiContext.get(getFullUrl(apiEndpoints.account.profile));
  
  if (!response.ok()) {
    throw new Error(` Get user profile failed with status ${response.status()}: ${await response.text()}`);
  }
  
  return response.json();
}

export default {
  setApiBaseUrl,
  login,
  createNote,
  deleteNoteById,
  getAllNotes,
  getUserProfile
};
