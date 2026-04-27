import { Customer } from '../aggregates/customer';
import { Id } from '../../shared/value-objects/id';

/** AddressService service. */
export class AddressService {

  create(input: Partial<Customer>): Customer { throw new Error('not implemented'); }

  findById(id: Id): Customer | null { throw new Error('not implemented'); }

  list(limit: number): Customer[] { throw new Error('not implemented'); }

  delete(id: Id): void { throw new Error('not implemented'); }
}
