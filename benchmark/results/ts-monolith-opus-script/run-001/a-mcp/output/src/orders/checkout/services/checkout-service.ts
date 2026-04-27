import { CheckoutSession } from '../value-objects/checkout-session';
import { Id } from '../../../shared/value-objects/id';

export class CheckoutService {

  create(input: Partial<CheckoutSession>): CheckoutSession { throw new Error('not implemented'); }

  findById(id: Id): CheckoutSession | null { throw new Error('not implemented'); }

  list(limit: number): CheckoutSession[] { throw new Error('not implemented'); }

  delete(id: Id): void { throw new Error('not implemented'); }
}
