import { Id } from '../../../shared/value-objects/Id';
import { CheckoutSession } from '../value-objects/CheckoutSession';

/** Applies and manages discounts during checkout. */
export class DiscountService {
  create(input: Partial<CheckoutSession>): CheckoutSession { throw new Error('not implemented'); }
  findById(id: Id): CheckoutSession | null { throw new Error('not implemented'); }
  list(limit: number): CheckoutSession[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
