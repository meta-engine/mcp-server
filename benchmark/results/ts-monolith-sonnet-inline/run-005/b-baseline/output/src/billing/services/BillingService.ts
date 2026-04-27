import { Id } from '../../shared/value-objects/Id';
import { Invoice } from '../aggregates/Invoice';

/** Manages invoice creation and billing operations. */
export class BillingService {
  create(input: Partial<Invoice>): Invoice { throw new Error('not implemented'); }
  findById(id: Id): Invoice | null { throw new Error('not implemented'); }
  list(limit: number): Invoice[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
