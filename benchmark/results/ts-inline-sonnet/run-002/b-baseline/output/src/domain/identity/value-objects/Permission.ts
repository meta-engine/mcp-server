/** Value object representing an access permission granted to a user. */
export interface Permission {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
