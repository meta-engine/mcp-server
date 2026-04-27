import { Id } from '../../../shared/value-objects/Id';
import { Cart } from '../aggregates/Cart';

/** Manages shopping cart operations. */
export class CartService {
  create(input: Partial<Cart>): Cart { throw new Error('not implemented'); }
  findById(id: Id): Cart | null { throw new Error('not implemented'); }
  list(limit: number): Cart[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
