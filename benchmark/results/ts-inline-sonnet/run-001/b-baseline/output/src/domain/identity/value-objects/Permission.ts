/** Permission value object representing an access control grant for a user. */
export interface Permission {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
