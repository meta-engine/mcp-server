/** Value object representing a permission granted to a user or role. */
export interface Permission {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
