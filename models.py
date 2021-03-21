import numpy as np


class KernelRidgeRegression:
    def __init__(self, kernel_func, Lambda=0.1):
        """
        Parameters
        ----------
            kernel_func : lambda function 
                a kernel function, takes two sets of vectors X_1 (n_1, m) and  X_2 (n_2, m)
                and returns the gram matrix K(X_1, X_2) (n_1, n_2)
                
            Lambda : float
                regularization parameter      
        """
        self.Kernel = kernel_func
        self.Alpha = None
        self.Data = None
        self.Lambda = Lambda
        print("Kernel Ridge Regression")
    
    def reset(self):
        self.Alpha = None
        self.Data = None
        
    def train(self, X, y):
        """
        Parameters
        ----------
            X : np.array. shape (n_samples, dim)
                training features
                
            y : np.array. shape (n_samples, 1)
                training targets
        """
        self.Data = X
        K = self.Kernel(X,X)
        n = K.shape[0]
        I = np.eye(n)
        self.Alpha = np.linalg.solve(K + self.Lambda*n*I, y)
        
    def predict(self, X):
        """
        Parameters
        ----------
            X : np.array. shape (n_samples, dim)
                features
                
        Returns
        -------
            y : np.array. shape (n_samples, 1)
                prediction
        """
        K = self.Kernel(X, self.Data)
        y = K @ self.Alpha
        return y


class KernelLogisticRegression:
    def __init__(self, kernel_func, Lambda=0.1, tol=1e-5, max_iter=100000, threshold=0.5):
        """
        Parameters
        ----------
            kernel_func : lambda function 
                a kernel function, takes two sets of vectors X_1 (n_1, m) and  X_2 (n_2, m)
                and returns the gram matrix K(X_1, X_2) (n_1, n_2)
                
            Lambda : float
                regularization parameter
                
            tol : float
                tolerance for stopping criteria
                
            max_iter : int
                maximum number of iterations allowed to converge
                
            threshold : float in [0, 1]
                probability threshold to predict 1
        """
        self.Kernel = kernel_func
        self.Alpha = None
        self.Data = None
        self.Lambda = Lambda
        self.tol = tol
        self.max_iter = max_iter
        self.threshold = threshold
        print("Kernel Logistic Regression")
    
    def reset(self):
        self.Alpha = None
        self.Data = None
        
    def loss(self, s):
        s = s.reshape(-1)
        l1 = -1/(1 + np.exp(s))
        l2 = np.exp(s)/(1 + np.exp(s))**2
        return np.diag(l1), np.diag(l2)
        
    def train(self, X, y):
        """
        Parameters
        ----------
            X : np.array. shape (n_samples, dim)
                training features
                
            y : np.array (int). shape (n_samples, 1)
                training labels in {-1, 1}
        """
        self.Data = X
        K = self.Kernel(X,X)
        n = K.shape[0]
        I = np.eye(n)
        
        alpha_old = np.zeros((n, 1))
        
        for step in range(self.max_iter):
            m = K @ alpha_old
            P, W = self.loss(y*m)
            z = W @ m - P @ y
            alpha_new = np.linalg.solve(W @ K + self.Lambda*n*I, z)
            
            error = np.linalg.norm(alpha_new - alpha_old)
            
            if error < self.tol:
                break
            else:
                alpha_old = alpha_new
                
        if (step == self.max_iter - 1) and (error > self.tol):
            print(f"Kernel Logistic Regression didn't converge ! you might want to take max_iter > {self.max_iter}")
    
        self.Alpha = alpha_new

    def predict(self, X):
        """
        Parameters
        ----------
            X : np.array. shape (n_samples, dim)
                features
                
        Returns
        -------
            y : np.array (int). shape (n_samples, 1)
                predicted labels in {-1, 1}
        """
        K = self.Kernel(X, self.Data)
        f = K @ self.Alpha
        p = 1/(1+np.exp(-f))
        y = (p>self.threshold).astype(int)
        return 2*y - 1