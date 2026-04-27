import { Id } from '../../shared/value-objects/Id';
import { Customer } from '../aggregates/Customer';

/** Manages customer account lifecycle. */
export class CustomerService {
  create(input: Partial<Customer>): Customer { throw new Error('not implemented'); }
  findById(id: Id): Customer | null { throw new Error('not implemented'); }
  list(limit: number): Customer[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
