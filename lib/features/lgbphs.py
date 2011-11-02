#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

import os, math
import torch


def compute(img_input, pos_input, features_output,
  CROP_EYES_D, CROP_H, CROP_W, CROP_OH, CROP_OW,
  GAMMA, SIGMA0, SIGMA1, SIZE, THRESHOLD, ALPHA,
  N_ORIENT, N_FREQ, FMAX, ORIENTATION_FULL, K, P, OPTIMAL_GAMMA_ETA,
  GAMMA_G, ETA_G, PF, CANCEL_DC, USE_ENVELOPE,
  BLOCK_H, BLOCK_W, OVERLAP_H, OVERLAP_W, RADIUS, P_N, CIRCULAR, 
  TO_AVERAGE, ADD_AVERAGE_BIT, UNIFORM, ROT_INV,
  first_annot, force):

  # Initializes cropper and destination array
  FEN = torch.ip.FaceEyesNorm( CROP_EYES_D, CROP_H, CROP_W, CROP_OH, CROP_OW)
  cropped_img = torch.core.array.float64_2(CROP_H, CROP_W)

  # Initializes the Tan and Triggs preprocessing
  TT = torch.ip.TanTriggs( GAMMA, SIGMA0, SIGMA1, SIZE, THRESHOLD, ALPHA)
  preprocessed_img = torch.core.array.float64_2(CROP_H, CROP_W)

  # Initializes the Gabor filterbank and the destination arrays
  GB = torch.ip.GaborBankFrequency( CROP_H, CROP_W, N_ORIENT, N_FREQ, FMAX, ORIENTATION_FULL, 
          K, P, OPTIMAL_GAMMA_ETA, GAMMA_G, ETA_G, PF, CANCEL_DC)
  if USE_ENVELOPE == False: GB.use_envelope = False
  gabor_imgs = torch.core.array.complex128_3( N_ORIENT*N_FREQ, CROP_H, CROP_W)
  gabor_imgs_mag_2d=[]
  for ig in range(0,N_ORIENT*N_FREQ):
    gabor_imgs_mag_2d.append(torch.core.array.float64_2( CROP_H, CROP_W))

  # Initializes LBPHS processor
  LBPHSF = torch.ip.LBPHSFeatures( BLOCK_H, BLOCK_W, OVERLAP_H, OVERLAP_W, RADIUS, P_N, CIRCULAR, TO_AVERAGE, ADD_AVERAGE_BIT, UNIFORM, ROT_INV)

  # Processes the 'dictionary of files'
  for k in img_input:
    print img_input[k]
    for ig in range(0,N_ORIENT*N_FREQ):
      if force == True and os.path.exists(features_output[ig][k]):
        print "Remove old features %s." % (features_output[ig][k])
        os.remove(features_output[ig][k])

    exist = True
    for ig in range(0,N_ORIENT*N_FREQ):
      if not os.path.exists(features_output[ig][k]):
        exist = False

    if exist:
      print "Features for sample %s already exists."  % (img_input[k])
    else:
      print "Computing features from sample %s." % (img_input[k])

      # Loads image file
      img_unk = torch.core.array.load( str(img_input[k]) )
      
      # Converts to grayscale
      if(img_unk.dimensions() == 3):
        img = torch.ip.rgb_to_gray(img_unk)
      else:
        img = img_unk

      # Input eyes position file
      annots = [int(j.strip()) for j in open(pos_input[k]).read().split()]
      if first_annot == 0: LW, LH, RW, RH = annots[0:4]
      else: nb_annots, LW, LH, RW, RH = annots[0:5]

      # Extracts and crops a face 
      FEN(img, cropped_img, LH, LW, RH, RW) 
       
      # Preprocesses a face using Tan and Triggs
      TT(cropped_img, preprocessed_img)
      preprocessed_img_s=preprocessed_img.convert('uint8', sourceRange=(-THRESHOLD,THRESHOLD))

      # Computes Gabor magnitude maps
      src_cplx = preprocessed_img_s.cast('complex128')
      # Calls the preprocessing algorithm
      GB(src_cplx, gabor_imgs)
      # Converts 3D array to a list of 2D arrays
      for x in range(gabor_imgs.extent(0)):
        for y in range(gabor_imgs.extent(1)):
          for z in range(gabor_imgs.extent(2)):
            gabor_imgs_mag_2d[x][y,z] = abs(gabor_imgs[x,y,z])
      
      for ig in range(0,len(gabor_imgs_mag_2d)):
        # Computes LBP histograms
        lbphs_blocks = LBPHSF(gabor_imgs_mag_2d[ig])
        lbphs_array = torch.core.array.int32_2(len(lbphs_blocks), LBPHSF.NBins)
        for bi in range(0,len(lbphs_blocks)):
          lbpb = lbphs_blocks[bi]
          for j in range(LBPHSF.NBins):
            lbphs_array[bi,j] = lbpb[j]
        # Saves to file
        lbphs_array.save(str(features_output[ig][k]))
