import { User } from "../aggregates/User";

/** UserRepository domain service for the identity domain. */
export class UserRepository {
  create(input: Partial<User>): User {
    void input;
    throw new Error("not implemented");
  }

  findById(id: string): User | null {
    void id;
    throw new Error("not implemented");
  }

  list(limit: number): User[] {
    void limit;
    throw new Error("not implemented");
  }

  delete(id: string): void {
    void id;
    throw new Error("not implemented");
  }
}
