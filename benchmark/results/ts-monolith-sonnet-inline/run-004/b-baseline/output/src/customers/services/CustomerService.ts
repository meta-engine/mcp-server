import { Id } from '../../shared/value-objects/Id';
import { Customer } from '../aggregates/Customer';

/** Manages customer accounts */
export class CustomerService {
  create(input: Partial<Customer>): Customer {
    void input;
    throw new Error('not implemented');
  }

  findById(id: Id): Customer | null {
    void id;
    throw new Error('not implemented');
  }

  list(limit: number): Customer[] {
    void limit;
    throw new Error('not implemented');
  }

  delete(id: Id): void {
    void id;
    throw new Error('not implemented');
  }
}
