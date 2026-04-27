import { Id } from '../../shared/value-objects/Id';
import { Customer } from '../aggregates/Customer';

/** Manages customer address records. */
export class AddressService {
  create(input: Partial<Customer>): Customer { throw new Error('not implemented'); }
  findById(id: Id): Customer | null { throw new Error('not implemented'); }
  list(limit: number): Customer[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
