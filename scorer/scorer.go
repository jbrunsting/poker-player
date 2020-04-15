package scorer

import (
	"fmt"
	"sort"

	"github.com/jbrunsting/poker-player/card"
)

const cardsToUse = 5

type HandType int

const (
	HandRoyalFlush    = 10
	HandStraightFlush = 9
	HandFourKind      = 8
	HandFullHouse     = 7
	HandFlush         = 6
	HandStraight      = 5
	HandThreeKind     = 4
	HandTwoPair       = 3
	HandPair          = 2
	HandHighCard      = 1
)

const (
	maxHand = 10
	minHand = 1
)

type tieResult int

const (
	lt = iota
	gt
	tie
)

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Cards must be sorted in descending order
func tiebreaker(cardsA []card.Card, aAceHi bool, cardsB []card.Card, bAceHi bool) tieResult {
	cards := [][]card.Card{cardsA, cardsB}
	ace_hi := []bool{aAceHi, bAceHi}

	rankings := make([][]int, 2)
	for i := range rankings {
		for _, c := range cards[i] {
			v := c.Val
			if v == card.AceVal && !ace_hi[i] {
				v = card.AceLowVal
			}
			rankings[i] = append(rankings[i], v)
		}
		sort.Sort(sort.Reverse(sort.IntSlice(rankings[i])))
	}

	for i := 0; i < min(len(rankings[0]), len(rankings[1])); i++ {
		if rankings[0][i] < rankings[1][i] {
			return lt
		} else if rankings[0][i] > rankings[1][i] {
			return gt
		}
	}

	if len(rankings[0]) < len(rankings[1]) {
		return lt
	} else if len(rankings[0]) > len(rankings[1]) {
		return gt

	}

	return tie
}

type Score struct {
	Type      HandType
	HandCards []card.Card
	SideCards []card.Card
}

func handTypeToString(t HandType) string {
	if t == HandRoyalFlush {
		return "royalFlush"
	} else if t == HandStraightFlush {
		return "straightFlush"
	} else if t == HandFourKind {
		return "fourKind"
	} else if t == HandFullHouse {
		return "fullHouse"
	} else if t == HandFlush {
		return "flush"
	} else if t == HandStraight {
		return "straight"
	} else if t == HandThreeKind {
		return "threeKind"
	} else if t == HandTwoPair {
		return "twoPair"
	} else if t == HandPair {
		return "pair"
	} else if t == HandHighCard {
		return "highCard"
	}
	return "unknown"
}

func (s Score) String() string {
	typeName := ""
	if s.Type == HandRoyalFlush {
		typeName = "royalFlush"
	} else if s.Type == HandStraightFlush {
		typeName = "straightFlush"
	} else if s.Type == HandFourKind {
		typeName = "fourKind"
	} else if s.Type == HandFullHouse {
		typeName = "fullHouse"
	} else if s.Type == HandFlush {
		typeName = "flush"
	} else if s.Type == HandStraight {
		typeName = "straight"
	} else if s.Type == HandThreeKind {
		typeName = "threeKind"
	} else if s.Type == HandTwoPair {
		typeName = "twoPair"
	} else if s.Type == HandPair {
		typeName = "pair"
	} else if s.Type == HandHighCard {
		typeName = "highCard"
	}
	return typeName
}

func (s *Score) Equals(o *Score) bool {
	return !s.LessThan(o) && !o.LessThan(s)
}

func (s *Score) LessThan(o *Score) bool {
	if s.Type != o.Type {
		return s.Type < o.Type

	}
	// Tiebreaker
	sAceHi := true
	oAceHi := true
	// Ace is low iff we have a straight with the ace at the bottom (no king
	// in the straight)
	if s.Type == HandStraight && card.HasCard(s.HandCards, card.AceVal-1) {
		sAceHi = false
	}
	if o.Type == HandStraight && card.HasCard(o.HandCards, card.AceVal-1) {
		oAceHi = false

	}
	handTiebreaker := tiebreaker(s.HandCards, sAceHi, o.HandCards, oAceHi)
	if handTiebreaker != tie {
		return handTiebreaker == lt
	}

	sideTiebreaker := tiebreaker(
		s.SideCards,
		false,
		o.SideCards,
		false,
	)
	return sideTiebreaker == lt
}

func findNKind(cards []card.Card, n int) []card.Card {
	numSequential := 1
	for i := len(cards) - 2; i >= 0; i-- {
		if cards[i].Val == cards[i+1].Val {
			numSequential++
		} else {
			numSequential = 1
		}
		if numSequential == n {
			return cards[i : i+n]
		}
	}
	return []card.Card{}
}

func filterCards(cards []card.Card, filter func(card.Card) bool) []card.Card {
	filtered := []card.Card{}
	for _, c := range cards {
		if filter(c) {
			filtered = append(filtered, c)
		}
	}
	return filtered
}

func maxVal(cards []card.Card) int {
	maxVal := cards[0].Val
	for _, c := range cards {
		if c.Val > maxVal {
			maxVal = c.Val
		}
	}
	return maxVal
}

// Returns empty list if not found
func findHand(cards []card.Card, hand HandType) []card.Card {
	sort.Slice(cards, func(i, j int) bool {
		return cards[i].Val > cards[j].Val
	})
	return _findHand(cards, hand)
}

func _findHand(cards []card.Card, hand HandType) []card.Card {
	if hand == HandRoyalFlush {
		royalCards := filterCards(cards, func(c card.Card) bool {
			return c.Val >= 10
		})
		return findHand(royalCards, HandStraightFlush)
	} else if hand == HandStraightFlush {
		// We do this whole bestStraight thing to account for cases where we
		// have 10 cards or more, since in those cases we could have multiple
		// suits with a straight flush and we should pick the best one
		bestStraight := []card.Card{}
		for suit := 0; suit < card.NumSuits; suit++ {
			suitCards := filterCards(cards, func(c card.Card) bool {
				return c.Suit == suit
			})
			straightCards := findHand(suitCards, HandStraight)
			if len(straightCards) != 0 &&
				(len(bestStraight) == 0 || maxVal(bestStraight) < maxVal(straightCards)) {
				bestStraight = straightCards
			}
		}
		return bestStraight
	} else if hand == HandFourKind {
		return findNKind(cards, 4)
	} else if hand == HandFullHouse {
		threeKindCards := findHand(cards, HandThreeKind)
		if len(threeKindCards) != 0 {
			otherCards := filterCards(cards, func(c card.Card) bool {
				for _, o := range threeKindCards {
					if c == o {
						return false
					}
				}
				return true
			})
			pairCards := findHand(otherCards, HandPair)
			if len(pairCards) != 0 {
				return append(threeKindCards, pairCards...)
			}
		}
		return []card.Card{}
	} else if hand == HandFlush {
		bestFlush := []card.Card{}
		for suit := 0; suit < card.NumSuits; suit++ {
			suitCards := filterCards(cards, func(c card.Card) bool {
				return c.Suit == suit
			})
			if len(suitCards) >= 5 {
				flushCards := suitCards[:5]
				if len(flushCards) != 0 && (len(bestFlush) == 0 || maxVal(bestFlush) < maxVal(flushCards)) {
					bestFlush = flushCards
				}
			}
		}
		return bestFlush
	} else if hand == HandStraight {
		if len(cards) < 5 {
			return []card.Card{}
		}
		numSequential := 1
		for i := 0; i < len(cards)-1; i++ {
			if cards[i].Val == cards[i+1].Val+1 {
				numSequential++
			} else if cards[i].Val != cards[i+1].Val {
				numSequential = 1
			}
			if numSequential == 5 {
				return cards[i-3 : i+2]
			}
		}
		if numSequential == 4 && cards[0].Val == card.MinVal && cards[len(cards)-1].Val == card.AceVal {
			return append([]card.Card{card.Card{cards[len(cards)-1].Suit, card.AceVal}}, cards[0:4]...)
		}
		return nil
	} else if hand == HandThreeKind {
		return findNKind(cards, 3)
	} else if hand == HandTwoPair {
		pair1Cards := findHand(cards, HandPair)
		if len(pair1Cards) != 0 {
			otherCards := filterCards(cards, func(c card.Card) bool {
				for _, o := range pair1Cards {
					if c == o {
						return false
					}
				}
				return true
			})
			pair2Cards := findHand(otherCards, HandPair)
			if len(pair2Cards) != 0 {
				return append(pair1Cards, pair2Cards...)
			}
		}
		return []card.Card{}
	} else if hand == HandPair {
		return findNKind(cards, 2)
	} else if hand == HandHighCard {
		return cards[0:1]
	}

	return []card.Card{}
}

func GetScore(cards []card.Card) Score {
	for i1, o1 := range cards {
		for i2, o2 := range cards {
			if i1 != i2 && o1 == o2 {
				panic(fmt.Sprintf("DUPLICATE for cards %v, card %s at %d, %d", cards, o1, i1, i2))
			}
		}
	}
	for i := maxHand + 1; i >= minHand; i-- {
		handType := HandType(i)
		handCards := findHand(cards, handType)
		sideCards := filterCards(cards, func(c card.Card) bool {
			for _, o := range handCards {
				if c == o {
					return false
				}
			}
			return true
		})
		if len(handCards) != 0 {
			return Score{handType, handCards, sideCards[:cardsToUse-len(handCards)]}
		}
	}
	panic("No score found")
}
