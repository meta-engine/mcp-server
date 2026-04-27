import { User } from '../aggregates/User';

/** UserRepository service. */
export class UserRepository {
  create(input: Partial<User>): User { throw new Error('not implemented'); }
  findById(id: string): User | null { throw new Error('not implemented'); }
  list(limit: number): User[] { throw new Error('not implemented'); }
  delete(id: string): void { throw new Error('not implemented'); }
}
