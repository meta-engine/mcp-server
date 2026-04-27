import { Cart } from '../aggregates/cart';
import { Id } from '../../../shared/value-objects/id';

/** CartService service. */
export class CartService {

  create(input: Partial<Cart>): Cart { throw new Error('not implemented'); }

  findById(id: Id): Cart | null { throw new Error('not implemented'); }

  list(limit: number): Cart[] { throw new Error('not implemented'); }

  delete(id: Id): void { throw new Error('not implemented'); }
}
