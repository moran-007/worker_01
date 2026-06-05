export function hasPermission(user, permission) {
  return Array.isArray(user?.permissions) && user.permissions.includes(permission)
}

export function hasAnyPermission(user, permissions) {
  return permissions.some((permission) => hasPermission(user, permission))
}
