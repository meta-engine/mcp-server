import { User } from '../aggregates/User';

/** Service providing business operations for users. */
export class UserService {
  create(input: Partial<User>): User {
    void input;
    throw new Error('not implemented');
  }

  findById(id: string): User | null {
    void id;
    throw new Error('not implemented');
  }

  list(limit: number): User[] {
    void limit;
    throw new Error('not implemented');
  }

  delete(id: string): void {
    void id;
    throw new Error('not implemented');
  }
}
