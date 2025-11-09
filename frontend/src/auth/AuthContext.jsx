import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

const API_BASE_URL = "http://localhost:8000";
const TOKEN_STORAGE_KEY = "lifemate.jwt";

const AuthContext = createContext(null);

function resolveUrl(path) {
  if (typeof path !== "string") {
    return path;
  }
  if (path.startsWith("http://") || path.startsWith("https://")) {
    return path;
  }
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalized}`;
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  const [initializing, setInitializing] = useState(true);
  const [loginLoading, setLoginLoading] = useState(false);

  const clearAuthState = useCallback(() => {
    setToken(null);
    setUser(null);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }, []);

  const logout = useCallback(() => {
    clearAuthState();
  }, [clearAuthState]);

  const fetchCurrentUser = useCallback(async (tokenValue) => {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        Authorization: `Bearer ${tokenValue}`,
      },
    });
    if (!response.ok) {
      throw new Error("Unable to load user profile");
    }
    const data = await response.json();
    setUser(data);
    return data;
  }, []);

  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!storedToken) {
      setInitializing(false);
      return;
    }
    setToken(storedToken);
    fetchCurrentUser(storedToken)
      .catch(() => {
        clearAuthState();
      })
      .finally(() => {
        setInitializing(false);
      });
  }, [fetchCurrentUser, clearAuthState]);

  const login = useCallback(
    async (username, password) => {
      setLoginLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/auth/login`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password }),
        });

        if (!response.ok) {
          let message = "Login failed";
          try {
            const data = await response.json();
            if (data?.detail) {
              message = data.detail;
            }
          } catch (jsonError) {
            const text = await response.text();
            if (text) {
              message = text;
            }
          }
          throw new Error(message);
        }

        const { access_token: accessToken } = await response.json();
        if (!accessToken) {
          throw new Error("Login response did not include an access token");
        }
        localStorage.setItem(TOKEN_STORAGE_KEY, accessToken);
        setToken(accessToken);
        const currentUser = await fetchCurrentUser(accessToken);
        setInitializing(false);
        return currentUser;
      } catch (error) {
        clearAuthState();
        setInitializing(false);
        throw error;
      } finally {
        setLoginLoading(false);
      }
    },
    [fetchCurrentUser, clearAuthState]
  );

  const handleUnauthorized = useCallback(() => {
    clearAuthState();
    setInitializing(false);
  }, [clearAuthState]);

  const apiFetch = useCallback(
    async (path, options = {}) => {
      if (!token) {
        handleUnauthorized();
        throw new Error("unauthorized");
      }
      const url = resolveUrl(path);
      const headers = new Headers(options.headers || {});
      headers.set("Authorization", `Bearer ${token}`);
      const response = await fetch(url, {
        ...options,
        headers,
      });
      if (response.status === 401) {
        handleUnauthorized();
        throw new Error("unauthorized");
      }
      return response;
    },
    [token, handleUnauthorized]
  );

  const value = useMemo(
    () => ({
      apiFetch,
      initializing,
      isAuthenticated: Boolean(token && user),
      login,
      loginLoading,
      logout,
      token,
      user,
    }),
    [apiFetch, initializing, login, loginLoading, logout, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export { API_BASE_URL };
