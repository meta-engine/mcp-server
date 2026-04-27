import { User } from '../aggregates/User';

/** TokenService service. */
export class TokenService {
  create(input: Partial<User>): User { throw new Error('not implemented'); }
  findById(id: string): User | null { throw new Error('not implemented'); }
  list(limit: number): User[] { throw new Error('not implemented'); }
  delete(id: string): void { throw new Error('not implemented'); }
}
