/** Value object representing a user's profile information. */
export interface Profile {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
