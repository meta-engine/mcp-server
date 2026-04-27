/** Value object representing a user's public profile information. */
export interface Profile {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
