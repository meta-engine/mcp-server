import { Id } from '../../shared/value-objects/Id';
import { Invoice } from '../aggregates/Invoice';

/** Gateway for processing payments against invoices. */
export class PaymentGateway {
  create(input: Partial<Invoice>): Invoice { throw new Error('not implemented'); }
  findById(id: Id): Invoice | null { throw new Error('not implemented'); }
  list(limit: number): Invoice[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
