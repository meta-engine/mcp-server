/** Profile value object representing a user's public identity information. */
export interface Profile {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
