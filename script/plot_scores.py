#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 10 Nov 2011 08:33:57 CET 

"""Plot scores for different groups of data.
"""

import os
import sys
import matplotlib.pyplot as mpl
import bob
import argparse

def main():

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('baseline', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the baseline face verification')
  parser.add_argument('overlay', metavar='FILE', type=str,
      default="", help='Name of the scores file (4-column) containing the scores for the overlaid negatives (spoofing attacks)')
  parser.add_argument('-p', '--overlay-protocol', metavar='STR', type=str,
      dest='protocol', default="", help='Legend that will be used for the overlaied negatives (spoofing attacks)')
  parser.add_argument('-t', '--title', metavar='STR', type=str,
      dest='title', default="", help='Plot title')
  parser.add_argument('-l', '--line', metavar='FLOAT', type=float,
      dest='line', help='If set, draws a vertical line on the plot (to indicate a threshold)')
  parser.add_argument('-L', '--line-legend', metavar='STR', type=str,
      default='threshold', dest='lineleg', help='If you set a vertical line to be created on the plot, you can set a legend for it using this flag. Otherwise, it will just say "%(default)s"')

  args = parser.parse_args()

  if not args.title: 
    args.title = os.path.splitext(os.path.basename(args.overlay))[0]
  if not args.protocol: 
    args.protocol = os.path.splitext(os.path.basename(args.overlay))[0]

  [base_neg, base_pos] = bob.measure.load.split_four_column(args.baseline)
  [over_neg, over_pos] = bob.measure.load.split_four_column(args.overlay)

  mpl.hist(base_neg, bins=10, color='red', alpha=0.5, label="Impostors",
      normed=True)
  mpl.hist(base_pos, bins=20, color='blue', alpha=0.5, label="True Clients",
      normed=True)
  mpl.hist(over_neg, bins=20, color='black', alpha=0.5, label=args.protocol,
      normed=True)
  if args.line is not None:
    ax = mpl.axis()
    mpl.axvline(x=args.line, ymin=ax[2], ymax=ax[3], linewidth=2,
        color='green', linestyle='--', label=args.lineleg)

  mpl.title(args.title)
  mpl.xlabel("Verification Scores")
  mpl.ylabel("Normalized Count")
  mpl.grid()
  mpl.legend()
  mpl.savefig("score-dist.pdf")

if __name__ == '__main__':
  main()
