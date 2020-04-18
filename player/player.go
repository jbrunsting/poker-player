package player

type GameRound int

const (
	RoundPreFlop = 0
	RoundFlop    = 1
	RoundTurn    = 2
	RoundRiver   = 3
)

const NumRounds = 4

type Player struct {
	Name          string
	Wins          int
	FoldsPerRound []int
}

func (p *Player) Init(name string) {
	p.Name = name
	p.Wins = 0
	p.FoldsPerRound = []int{}
	for i := 0; i < NumRounds; i++ {
		p.FoldsPerRound = append(p.FoldsPerRound, 0)
	}
}
