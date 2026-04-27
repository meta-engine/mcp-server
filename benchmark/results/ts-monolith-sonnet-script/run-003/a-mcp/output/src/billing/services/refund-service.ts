import { Invoice } from '../aggregates/invoice';
import { Id } from '../../shared/value-objects/id';

export class RefundService {

  create(input: Partial<Invoice>): Invoice { throw new Error('not implemented'); }

  findById(id: Id): Invoice | null { throw new Error('not implemented'); }

  list(limit: number): Invoice[] { throw new Error('not implemented'); }

  delete(id: Id): void { throw new Error('not implemented'); }
}
