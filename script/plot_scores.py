#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 10 Nov 2011 08:33:57 CET 

"""Plot scores for different groups of data.
"""

import os
import sys
import matplotlib.pyplot as mpl
import torch
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

  args = parser.parse_args()

  if not args.title: 
    args.title = os.path.splitext(os.path.basename(args.overlay))[0]
  if not args.protocol: 
    args.protocol = os.path.splitext(os.path.basename(args.overlay))[0]

  [base_neg, base_pos] = torch.measure.load.split_four_column(args.baseline)
  [over_neg, over_pos] = torch.measure.load.split_four_column(args.overlay)

  mpl.hist(base_neg, bins=10, color='red', alpha=0.5, label="Impostors",
      normed=True)
  mpl.hist(base_pos, bins=20, color='blue', alpha=0.5, label="True Clients",
      normed=True)
  mpl.hist(over_neg, bins=20, color='black', alpha=0.5, label=args.protocol,
      normed=True)

  mpl.title(args.title)
  mpl.xlabel("Verification Scores")
  mpl.ylabel("Normalized Count")
  mpl.grid()
  mpl.legend()
  mpl.savefig("score-dist.pdf")

if __name__ == '__main__':
  main()
