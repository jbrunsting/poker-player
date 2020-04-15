package main

import (
	"bufio"
	"fmt"
	"os"

	"github.com/jbrunsting/poker-player/card"
	"github.com/jbrunsting/poker-player/command"
	"github.com/jbrunsting/poker-player/scorer"
)

type gameOutcome int

const (
	win = iota
	loss
	tie
)

const (
	handSize        = 2
	tableSize       = 5
	predictionIters = 50000
)

func addCardParams(cards []card.Card, params []command.Param) []card.Card {
	for _, p := range params {
		cards = append(cards, *p.Card)
	}
	return cards
}

func predict(deck *card.Deck, hand []card.Card, table []card.Card, players int) {
	outcomeCounts := make([]int, 3)
	for i := 0; i < predictionIters; i++ {
		deck.Reshuffle()
		paddedHand := card.PadWithDeck(hand, handSize, deck)
		paddedTable := card.PadWithDeck(table, tableSize, deck)
		playerHands := make([][]card.Card, players-1)
		for i := 0; i < players-1; i++ {
			playerHands[i] = card.PadWithDeck([]card.Card{}, handSize, deck)
		}
		outcome := win
		curCards := []card.Card{}
		curCards = append(curCards, paddedTable...)
		curCards = append(curCards, paddedHand...)
		handScore := scorer.GetScore(curCards)
		for _, ph := range playerHands {
			curCards = []card.Card{}
			curCards = append(curCards, paddedTable...)
			curCards = append(curCards, ph...)
			phScore := scorer.GetScore(curCards)
			if handScore.LessThan(&phScore) {
				outcome = loss
				break
			} else if handScore.Equals(&phScore) {
				outcome = tie
			}
		}

		outcomeCounts[outcome] += 1
	}
	outcomePercents := make([]float64, 3)
	for i := 0; i < 3; i++ {
		outcomePercents[i] = float64(outcomeCounts[i]) / float64(predictionIters)
	}

	fmt.Printf("Odds for hand [%v] with table [%v] and %d players:\n",
		card.CardsStr(hand), card.CardsStr(table), players)
	fmt.Printf("    Win:  %f\n    Loss: %f\n    Tie:  %f\n",
		outcomePercents[win], outcomePercents[loss], outcomePercents[tie])
}

func main() {
	players := 0
	hand := []card.Card{}
	flop := []card.Card{}
	turn := []card.Card{}
	river := []card.Card{}

	getTable := func() []card.Card {
		table := append(flop, turn...)
		table = append(table, river...)
		return table
	}
	printTable := func() {
		table := getTable()
		fmt.Printf("Table is %s\n", card.CardsStr(table))
	}

	commands := make([]command.Command, 0)

	setPlayers := func(params []command.Param) {
		players = params[0].Number
		if params[0].Number <= 0 {
			return
		}
		fmt.Printf("There are %d players\n", players)
	}
	setHand := func(params []command.Param) {
		if players == 0 {
			fmt.Printf("Must set the number of players before your hand\n")
			return
		}
		hand = []card.Card{}
		hand = addCardParams(hand, params)
		fmt.Printf("Hand is %s\n", card.CardsStr(hand))
	}
	setFlop := func(params []command.Param) {
		if len(hand) == 0 {
			fmt.Printf("Must set your hand before the flop\n")
			return
		}
		flop = []card.Card{}
		flop = addCardParams(flop, params)
		printTable()
	}
	setTurn := func(params []command.Param) {
		if len(flop) == 0 {
			fmt.Printf("Must set the flop before the turn\n")
			return
		}
		turn = []card.Card{}
		turn = addCardParams(turn, params)
		printTable()
	}
	setRiver := func(params []command.Param) {
		if len(turn) == 0 {
			fmt.Printf("Must set the turn before the river\n")
			return
		}
		river = []card.Card{}
		river = addCardParams(river, params)
		printTable()
	}
	reset := func(params []command.Param) {
		players = 1
		hand = []card.Card{}
		flop = []card.Card{}
		turn = []card.Card{}
		river = []card.Card{}
		fmt.Println("Reset state")
	}
	makePrediction := func(params []command.Param) {
		fmt.Println("Making prediction")
		table := getTable()
		deck := card.Deck{}
		deck.Init()
		deck.Remove(hand)
		deck.Remove(table)
		predict(&deck, hand, table, players)
	}
	commandHelp := func(params []command.Param) {
		fmt.Printf("Commands are %s\n", commands)
	}

	commands = append(commands, command.Command{
		"players",
		[]command.ParamType{command.NumberParam},
		setPlayers,
	})
	commands = append(commands, command.Command{
		"hand",
		[]command.ParamType{command.CardParam, command.CardParam},
		setHand,
	})
	commands = append(commands, command.Command{
		"flop",
		[]command.ParamType{
			command.CardParam, command.CardParam, command.CardParam,
		},
		setFlop,
	})
	commands = append(commands, command.Command{
		"turn", []command.ParamType{command.CardParam}, setTurn,
	})
	commands = append(commands, command.Command{
		"river", []command.ParamType{command.CardParam}, setRiver,
	})
	commands = append(commands, command.Command{
		"reset", []command.ParamType{}, reset,
	})
	commands = append(commands, command.Command{
		"predict", []command.ParamType{}, makePrediction,
	})
	commands = append(commands, command.Command{
		"help", []command.ParamType{}, commandHelp,
	})

	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("> ")
		scanner.Scan()
		input := scanner.Text()
		if input == "quit" {
			return
		}

		for _, c := range commands {
			if c.Parse(input) {
				break
			}
		}
	}
}
