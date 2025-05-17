export type Card = {
  id: number,
  text: string
}

export type FullCard = Card & {collection_ids: number[]}