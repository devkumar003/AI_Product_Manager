export const validateEmail = (email: string): boolean => {
  if (!email) return false;
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
};

export const validatePassword = (password: string): boolean => {
  if (!password) return false;
  // At least 8 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character
  const re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$/;
  return re.test(password);
};

export const validateProjectName = (name: string): boolean => {
  if (!name) return false;
  const trimmed = name.trim();
  return trimmed.length >= 3 && trimmed.length <= 100;
};

export const validateDocumentTitle = (title: string): boolean => {
  if (!title) return false;
  const trimmed = title.trim();
  return trimmed.length >= 3 && trimmed.length <= 200;
};
