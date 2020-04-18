package main

import (
	"bufio"
	"fmt"
	"os"

	"github.com/jbrunsting/poker-player/card"
	"github.com/jbrunsting/poker-player/command"
	"github.com/jbrunsting/poker-player/player"
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
	predictionIters = 25000
)

func addCardParams(cards []card.Card, params []command.Param) []card.Card {
	for _, p := range params {
		cards = append(cards, *p.Card)
	}
	return cards
}

func predict(deck *card.Deck, hand []card.Card, table []card.Card, numPlayers int) {
	outcomeCounts := make([]int, 3)
	for i := 0; i < predictionIters; i++ {
		deck.Reshuffle()
		paddedHand := card.PadWithDeck(hand, handSize, deck)
		paddedTable := card.PadWithDeck(table, tableSize, deck)
		playerHands := make([][]card.Card, numPlayers-1)
		for i := 0; i < numPlayers-1; i++ {
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
		card.CardsStr(hand), card.CardsStr(table), numPlayers)
	fmt.Printf("    Win:  %f\n    Loss: %f\n    Tie:  %f\n",
		outcomePercents[win], outcomePercents[loss], outcomePercents[tie])
}

func main() {
	numPlayers := 0
	players := make(map[string]*player.Player)
	hand := []card.Card{}
	flop := []card.Card{}
	turn := []card.Card{}
	river := []card.Card{}

	getTable := func() []card.Card {
		table := append(flop, turn...)
		table = append(table, river...)
		return table
	}
	getRound := func() player.GameRound {
		if len(flop) == 0 {
			return player.RoundPreFlop
		} else if len(turn) == 0 {
			return player.RoundFlop
		} else if len(river) == 0 {
			return player.RoundTurn
		}
		return player.RoundRiver
	}
	printTable := func() {
		table := getTable()
		fmt.Printf("Table is %s\n", card.CardsStr(table))
	}

	commands := make([]command.Command, 0)

	resetCards := func() {
		hand = []card.Card{}
		flop = []card.Card{}
		turn = []card.Card{}
		river = []card.Card{}
	}
	makePrediction := func() {
		if numPlayers <= 0 {
			fmt.Println("Must have at least one player")
			return
		}
		fmt.Println("Making prediction")
		table := getTable()
		deck := card.Deck{}
		deck.Init()
		deck.Remove(hand)
		deck.Remove(table)
		predict(&deck, hand, table, numPlayers)
	}
	setPlayers := func(params []command.Param) {
		numPlayers = params[0].Number
		if params[0].Number <= 0 {
			return
		}
		fmt.Printf("There are %d players\n", numPlayers)
	}
	addName := func(params []command.Param) {
		name := params[0].String
		p := player.Player{}
		p.Init(name)
		players[name] = &p
	}
	removeName := func(params []command.Param) {
		delete(players, params[0].String)
	}
	foldName := func(params []command.Param) {
		// TODO: Do prefix matching
		players[params[0].String].FoldsPerRound[getRound()] += 1
	}
	wonName := func(params []command.Param) {
		players[params[0].String].Wins += 1
	}
	setHand := func(params []command.Param) {
		if numPlayers == 0 {
			fmt.Printf("Must set the number of players before your hand\n")
			return
		}
		if len(flop) != 0 || len(turn) != 0 || len(river) != 0 {
			fmt.Printf("Resetting cards for new hand")
			resetCards()
		}
		hand = []card.Card{}
		hand = addCardParams(hand, params)
		fmt.Printf("Hand is %s\n", card.CardsStr(hand))
		makePrediction()
	}
	setFlop := func(params []command.Param) {
		if len(hand) == 0 {
			fmt.Printf("Must set your hand before the flop\n")
			return
		}
		flop = []card.Card{}
		flop = addCardParams(flop, params)
		printTable()
		makePrediction()
	}
	setTurn := func(params []command.Param) {
		if len(flop) == 0 {
			fmt.Printf("Must set the flop before the turn\n")
			return
		}
		turn = []card.Card{}
		turn = addCardParams(turn, params)
		printTable()
		makePrediction()
	}
	setRiver := func(params []command.Param) {
		if len(turn) == 0 {
			fmt.Printf("Must set the turn before the river\n")
			return
		}
		river = []card.Card{}
		river = addCardParams(river, params)
		printTable()
		makePrediction()
	}
	reset := func() {
		resetCards()
		fmt.Println("Reset cards")
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
		"aname",
		[]command.ParamType{command.StringParam},
		addName,
	})
	commands = append(commands, command.Command{
		"rname",
		[]command.ParamType{command.StringParam},
		removeName,
	})
	commands = append(commands, command.Command{
		"folded",
		[]command.ParamType{command.StringParam},
		foldName,
	})
	commands = append(commands, command.Command{
		"won",
		[]command.ParamType{command.StringParam},
		wonName,
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
		"reset", []command.ParamType{}, func(params []command.Param) { reset() },
	})
	commands = append(commands, command.Command{
		"predict", []command.ParamType{}, func(params []command.Param) { makePrediction() },
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
