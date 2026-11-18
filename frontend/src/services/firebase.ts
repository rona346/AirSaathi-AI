import { initializeApp, getApps, FirebaseApp } from 'firebase/app';
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
  updateProfile,
  onAuthStateChanged,
  User,
  Auth,
} from 'firebase/auth';

const apiKey = import.meta.env.VITE_FIREBASE_API_KEY;
const authDomain = import.meta.env.VITE_FIREBASE_AUTH_DOMAIN;
const projectId = import.meta.env.VITE_FIREBASE_PROJECT_ID;
const appId = import.meta.env.VITE_FIREBASE_APP_ID;

// Validate that credentials exist and are not placeholder template text
const isConfigured = Boolean(
  apiKey &&
    projectId &&
    apiKey !== 'your_firebase_web_api_key_here' &&
    projectId !== 'your_firebase_project_id_here'
);

let app: FirebaseApp | null = null;
let auth: Auth | null = null;

if (isConfigured) {
  try {
    const existingApps = getApps();
    if (existingApps.length > 0) {
      app = existingApps[0];
    } else {
      app = initializeApp({
        apiKey,
        authDomain: authDomain || `${projectId}.firebaseapp.com`,
        projectId,
        appId: appId || undefined,
      });
    }
    auth = getAuth(app);
  } catch (err) {
    console.warn('Failed to initialize Firebase Web SDK. Running in Guest Mode.', err);
    auth = null;
    app = null;
  }
}

export function isFirebaseConfigured(): boolean {
  return isConfigured && auth !== null;
}

export async function registerWithEmailPassword(
  email: string,
  pass: string,
  displayName?: string
): Promise<User> {
  if (!auth) {
    throw new Error('Firebase authentication is not configured. Running in Guest / Demonstration mode.');
  }

  const credential = await createUserWithEmailAndPassword(auth, email.trim(), pass);
  if (displayName && credential.user) {
    try {
      await updateProfile(credential.user, { displayName: displayName.trim() });
    } catch (e) {
      console.warn('Could not update display name:', e);
    }
  }
  return credential.user;
}

export async function loginWithEmailPassword(email: string, pass: string): Promise<User> {
  if (!auth) {
    throw new Error('Firebase authentication is not configured. Running in Guest / Demonstration mode.');
  }

  const credential = await signInWithEmailAndPassword(auth, email.trim(), pass);
  return credential.user;
}

export async function logoutUser(): Promise<void> {
  if (auth) {
    await signOut(auth);
  }
}

export async function getCurrentIdToken(forceRefresh: boolean = false): Promise<string | null> {
  if (!auth || !auth.currentUser) {
    return null;
  }
  try {
    return await auth.currentUser.getIdToken(forceRefresh);
  } catch (err) {
    console.warn('Failed to retrieve Firebase ID token:', err);
    return null;
  }
}

export function onAuthStateListener(callback: (user: User | null) => void): () => void {
  if (!auth) {
    // Immediate callback for unconfigured guest state
    callback(null);
    return () => {};
  }
  return onAuthStateChanged(auth, callback);
}

export function getFriendlyAuthErrorMessage(errorCodeOrMessage: string): string {
  const code = (errorCodeOrMessage || '').toLowerCase();
  if (code.includes('auth/invalid-email')) {
    return 'Please enter a valid email address.';
  }
  if (code.includes('auth/user-not-found') || code.includes('auth/wrong-password') || code.includes('auth/invalid-credential')) {
    return 'Incorrect email or password. Please verify your credentials.';
  }
  if (code.includes('auth/email-already-in-use')) {
    return 'An account with this email address already exists. Please log in instead.';
  }
  if (code.includes('auth/weak-password')) {
    return 'Password is too weak. Please choose at least 6 characters.';
  }
  if (code.includes('auth/too-many-requests')) {
    return 'Access temporarily disabled due to multiple failed login attempts. Please try again later.';
  }
  if (code.includes('auth/network-request-failed')) {
    return 'Network connectivity error. Please check your internet connection.';
  }
  return errorCodeOrMessage || 'Authentication failed. Please try again.';
}
