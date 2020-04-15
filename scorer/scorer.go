package scorer

import (
	"sort"

	"github.com/jbrunsting/poker-player/card"
)

const cardsToUse = 5

type HandType int

const (
	royalFlush    = 10
	straightFlush = 9
	fourKind      = 8
	fullHouse     = 7
	flush         = 6
	straight      = 5
	threeKind     = 4
	twoPair       = 3
	pair          = 2
	highCard      = 1
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

func tiebreaker(cards_a []card.Card, aAceHi bool, cards_b []card.Card, bAceHi bool) tieResult {
	cards := [][]card.Card{cards_a, cards_b}
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

func (s Score) String() string {
	typeName := ""
	if s.Type == royalFlush {
		typeName = "royalFlush"
	} else if s.Type == straightFlush {
		typeName = "straightFlush"
	} else if s.Type == fourKind {
		typeName = "fourKind"
	} else if s.Type == fullHouse {
		typeName = "fullHouse"
	} else if s.Type == flush {
		typeName = "flush"
	} else if s.Type == straight {
		typeName = "straight"
	} else if s.Type == threeKind {
		typeName = "threeKind"
	} else if s.Type == twoPair {
		typeName = "twoPair"
	} else if s.Type == pair {
		typeName = "pair"
	} else if s.Type == highCard {
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
	// Ace is low iff we have a straight with the ace at the bottom (no
	// king in the straight)
	if s.Type == straight && card.HasCard(s.HandCards, card.AceVal-1) {
		sAceHi = false
	}
	if o.Type == straight && card.HasCard(o.HandCards, card.AceVal-1) {
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

func GetScore(cards []card.Card) Score {
	return Score{royalFlush, cards, cards}
}
