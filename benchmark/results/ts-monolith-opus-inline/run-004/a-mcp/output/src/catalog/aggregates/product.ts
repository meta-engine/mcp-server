import { Id } from '../../shared/value-objects/id';
import { Money } from '../../shared/value-objects/money';
import { ProductState } from '../enums/product-state.enum';

/** Product aggregate root for the catalog module. */
export class Product {

  constructor(public id: Id, public name: string, public price: Money, public state: ProductState) { }
}
