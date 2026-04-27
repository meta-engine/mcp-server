import { StockItem } from '../aggregates/stock-item';

export class StockService {

  create(input: Partial<StockItem>): StockItem { throw new Error('not implemented'); }

  findById(id: string): StockItem | null { throw new Error('not implemented'); }

  list(limit: number): StockItem[] { throw new Error('not implemented'); }

  delete(id: string): void { throw new Error('not implemented'); }
}
