/** Value object representing a discrete access permission granted to a user. */
export interface Permission {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
